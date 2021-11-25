import { Component, OnInit } from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {DrawModalComponent} from "../draw-modal/draw-modal.component";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  constructor(private dialog: MatDialog) { }

  ngOnInit(): void {
  }

  verify() {
    // check Username, pass with backend

    if (true) {
      this.init2FA();
    }

  }

  init2FA() {
    this.dialog.open(DrawModalComponent, {
      data: {
        "loginToken": "someToken",
        "deviceId": "someDeviceId"
      }, width: '1100px', height: '700px'
    });
  }

}
