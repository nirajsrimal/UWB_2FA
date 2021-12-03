import { Component, OnInit } from '@angular/core';
import {Codec} from "../common";
import {HttpClient} from "@angular/common/http";
import {MatSnackBar} from "@angular/material/snack-bar";

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.css']
})
export class SignUpComponent implements OnInit {

  anyNavigator: any = undefined;

  selectedDevice: any = undefined;
  productId = undefined;
  vendorId = undefined;

  deviceReader: any = undefined;
  deviceWriter: any = undefined;

  searchedPhones = false;
  selectedPhone = undefined;
  phonesList = [];

  codec: Codec = new Codec();

  name: string = '';
  username: string = '';
  password: string = '';

  constructor(private http: HttpClient, private snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.anyNavigator = navigator;
  }

  raiseRequest() {
    if (!("serial" in this.anyNavigator)) {
      alert("Serial Port support does not exist in this browser");
    }

    this.anyNavigator.serial.requestPort().then(async (selectedDevice: any) => {
      this.selectedDevice = selectedDevice;
      const {usbProductId, usbVendorId} = this.selectedDevice.getInfo();

      this.productId = usbProductId;
      this.vendorId = usbVendorId;

      await this.selectedDevice.open({baudRate: 9600});

      this.searchedPhones = false;
      this.selectedPhone = undefined;
    }, (_: any) => {});
  }

  refresh() {
    this.deviceReader = this.selectedDevice.readable.getReader();
    this.deviceWriter = this.selectedDevice.writable.getWriter();
  }

  async scanPhones() {
    this.refresh();
    this.selectedPhone = undefined;
    this.phonesList = [];
    this.searchedPhones = false;

    await this.deviceWriter.write(this.codec.encode("getdlist"));
    this.deviceWriter.releaseLock();

    let response = "";
    while (true) {
      const timeoutReader = Promise.race([
        this.deviceReader.read(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 1000))
      ])
      try {
        const {value, done} = await timeoutReader;
        if (done) {
          this.deviceReader.releaseLock();
          break;
        }
        response += this.codec.decode(value);
      } catch (e) {
        this.deviceReader.cancel();
        this.deviceReader.releaseLock();
        break;
      }
    }

    this.populateDeviceList(response);
  }

  populateDeviceList(response: string) {
    this.searchedPhones = true;
    let lines = response.split("\n");
    for(const line of lines) {
      if (line.includes("DList")) {
        const start = line.indexOf("{");
        const end = line.indexOf("}");

        const objString = line.substr(start, end+1);
        this.phonesList = JSON.parse(objString)["DList"];
      }
    }
  }

  signup() {
    this.http.post('http://localhost:5000/signup', {
      'username': this.username,
      'password': this.password,
      'name': this.name,
      'tag_id': this.selectedPhone
    }).subscribe({
      next: (_) => {
        this.snackBar.open("Successfully signed up. Please present this device at login!",
          undefined, {duration: 3000}
        );
      },
      error: (err) => {
        this.snackBar.open("Failed to signup. Please use a unique username.", undefined,
          {duration: 5000}
        );
        console.error("Unsuccessful signup", err);
      }
    });
  }
}
