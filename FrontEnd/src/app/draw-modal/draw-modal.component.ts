import {Component, Inject, OnDestroy, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {Codec} from "../common";
import {io, Socket} from 'socket.io-client';
import {MatSnackBar} from '@angular/material/snack-bar';

@Component({
  selector: 'app-draw-modal',
  templateUrl: './draw-modal.component.html',
  styleUrls: ['./draw-modal.component.css']
})
export class DrawModalComponent implements OnInit, OnDestroy {

  // Graph data
  xData: number[] = []
  yData: number[] = []
  xs: number[] = []
  ys: number[] = []
  graph: {data: any[], layout: any} | undefined = undefined;
  shape: string = '';

  // Receiver members
  selectedReceiver: any = undefined;
  anyNavigator: any = undefined;
  deviceReader: any = undefined;
  deviceWriter: any = undefined;
  socket: Socket | undefined = undefined;
  port: any = undefined;

  // Target members
  targetPhoneFound: boolean = false;
  failedToFindPhone: boolean = false;
  recording: boolean = false;
  evNum: number = 0;

  codec: Codec = new Codec();

  name: string = '';
  token: string = '';
  tokenVerified: boolean = false;

  constructor(@Inject(MAT_DIALOG_DATA) public data: any, private snackBar: MatSnackBar) {
    this.regenerateGraph();
  }

  ngOnInit(): void {
    this.anyNavigator = navigator;
  }

  async ngOnDestroy() {
    this.recording = false;
    if (this.selectedReceiver) {
      await this.selectedReceiver.close();
    }
    if (this.deviceWriter) {
      try {
        this.deviceWriter.releaseLock();
      } catch (_) {}
    }

    if (this.deviceReader) {
      try {
        this.deviceReader.cancel();
        this.deviceReader.releaseLock();
      } catch (_) {}
    }
  }

  regenerateGraph(newX?:number, newY?:number) {
    let window = 5;
    if (newX && newY) {
      this.xs.push(newX)
      this.ys.push(newY)
      let data_len = this.xs.length;
      if(data_len >= window) {

        this.xs = this.xs.slice(Math.max(this.xs.length - window, 0));
        this.ys = this.ys.slice(Math.max(this.ys.length - window, 0));

        const sum_x = this.xs.reduce((prev, curr) => prev + curr, 0);
        const sum_y= this.ys.reduce((prev, curr) => prev + curr, 0);

        this.xData = [...this.xData];
        this.yData = [...this.yData];

        const xPoint = sum_x / window;
        const yPoint = sum_y / window
        this.xData.push(xPoint);
        this.yData.push(yPoint);

        if (this.socket) {
          this.socket.emit("data", {
            "x": xPoint,
            "y": yPoint,
            "ev_num": this.evNum++
          });
        }

      }
    }

    this.graph = {
      data: [
        { x: this.xData, y: this.yData, type: 'scatter', mode: 'lines+points', marker: {color: 'red'} }
      ],
      layout: {width: 400, height: 400, title: 'Detected Motion', bordercolor:'#000',
        xaxis:{range: [-20, 100], fixedrange: true, showgrid:false, zeroline:false, visible:false, mirror: true},
        yaxis:{range: [-10, 150], fixedrange: true, showgrid:false, zeroline:false, visible:false, mirror: true}}
    };
  }

  attachReceiver() {
    this.anyNavigator.serial.requestPort().then(async (selectedDevice: any) => {
      this.selectedReceiver = selectedDevice;
      await this.selectedReceiver.open({baudRate: 9600});
      await this.lookupDevice();
    }, (_: any) => {});
  }

  refresh() {
    this.deviceReader = this.selectedReceiver.readable.getReader();
    this.deviceWriter = this.selectedReceiver.writable.getWriter();
  }

  process(accum: string) {
    const lines = accum.split("\n");
    for(const line of lines.filter(item => item.length > 0)) {
      if (line.includes("TWR") && line.includes("}}")) {
        const start = line.lastIndexOf("{");
        const end = line.lastIndexOf("}");

        const received = JSON.parse(line.substr(start, end-start));

        this.regenerateGraph(received.Xcm, received.Ycm);
      }
    }
  }

  async startRecording() {
    this.refresh();
    this.recording = true;

    let response = ""
    while (this.recording) {
      const timeoutReader = Promise.race([
        this.deviceReader.read(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
      ]);

      try {
        const {value, done} = await timeoutReader;
        response += this.codec.decode(value);
        if (response.includes("\n")) {
          this.process(response);
          response = response.substr(response.lastIndexOf("\n")+1);
        }
        if (done) {
          break;
        }
      } catch (e) {
        this.deviceReader.cancel();
        this.deviceReader.releaseLock();
        break;
      }
    }
    try {
      this.deviceReader.cancel();
      this.deviceReader.releaseLock();
    } catch (e) {}
  }

  connectWithToken() {
    this.socket = io('ws://localhost:5000');
    this.socket.on("connect", () => {
      console.log("Starting pattern detection");
      // @ts-ignore
      this.socket.emit("token", this.token);
    });

    this.socket.on("token_ack", (shape) =>
    {
      this.tokenVerified = true;
      this.shape = shape;
    });

    this.socket.on("computed_result", (result) => {
      console.log(result);
      if (result['success'] == 'true') {
        localStorage.setItem('token', result['token']);
        this.snackBar.open("Successfully logged in!", undefined, {duration: 5000});

      } else {
        this.snackBar.open("Could not validate pattern. Please retry.",
          undefined, {duration: 5000});
        this.retry();
      }
    });
  }

  async lookupDevice() {
    this.refresh();
    this.name = this.data.name;
    this.targetPhoneFound = false;
    this.failedToFindPhone = false;

    const lookFor = this.data.deviceId;
    const joinMessage = `ADDTAG ${lookFor} 1000 4 64 1`;
    await this.deviceWriter.write(this.codec.encode(joinMessage));
    this.deviceWriter.releaseLock();

    let response = "";
    while (true) {
      const timeoutReader = Promise.race([
        this.deviceReader.read(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
      ])
      try {
        const {value, done} = await timeoutReader;
        response += this.codec.decode(value);
        if (done || response.includes("TWR")) {
          this.deviceReader.releaseLock();
          break;
        }
      } catch (e) {
        this.deviceReader.cancel();
        this.deviceReader.releaseLock();
        break;
      }
    }

    if (!response.includes("TWR")) {
      this.failedToFindPhone = true;
      this.snackBar.open("Could not detect registered device. Please make sure it's near you.", undefined,
        {duration: 5000}
      );
    } else {
      this.snackBar.open(`Detected registered device! Welcome ${this.name}!`, undefined,
        {duration: 5000}
      );
      this.targetPhoneFound = true;
      this.token = this.data.token;
      this.connectWithToken();
    }
  }

  retry() {
    this.xData = [];
    this.yData = [];
    this.evNum = 0;
    this.socket?.emit("retry");
  }

  finalize() {
    this.recording = false;
    this.snackBar.open("Please wait...", undefined, {duration: 3000});
    this.socket?.emit("finalize");
  }
}
