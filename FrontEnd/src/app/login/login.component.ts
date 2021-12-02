import { Component, OnInit } from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {DrawModalComponent} from "../draw-modal/draw-modal.component";
import {HttpClient} from "@angular/common/http";
import {LoginResponse} from "../common";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  username: string = '';
  password: string = '';

  constructor(private dialog: MatDialog, private http: HttpClient) { }

  ngOnInit(): void {
  }

  verify() {

    this.http.post<LoginResponse>('http://localhost:5000/login', {
      'username': this.username,
      'password': this.password
    }).subscribe({
      next: (resp: LoginResponse) => {
        console.log("Success verification");
        this.init2FA(resp['name'], resp['tag_id'], resp['token']);
      },
      error: (err) => {
        console.log("Unsuccessful verification");
      }
    });

  }

  init2FA(name: string, tagId: string, token: string) {
    this.dialog.open(DrawModalComponent, {
      data: {
        "name": name,
        "token": token,
        "deviceId": tagId
      }, width: '1100px', height: '650px'
    });
  }

}
