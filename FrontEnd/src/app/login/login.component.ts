import { Component, OnInit } from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {DrawModalComponent} from "../draw-modal/draw-modal.component";
import {HttpClient} from "@angular/common/http";
import {LoginResponse} from "../common";
import {MatSnackBar} from "@angular/material/snack-bar";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  username: string = '';
  password: string = '';

  constructor(private dialog: MatDialog, private http: HttpClient, private snackBar: MatSnackBar) { }

  ngOnInit(): void {
    localStorage.removeItem('token');
  }

  verify() {

    this.http.post<LoginResponse>('http://localhost:5000/login', {
      'username': this.username,
      'password': this.password
    }).subscribe({
      next: (resp: LoginResponse) => {
        this.snackBar.open("Successfully verified credentials. Initializing 2FA.", undefined,
          {duration: 5000}
        );
        this.init2FA(resp['name'], resp['tag_id'], resp['token']);
      },
      error: (err) => {
        this.snackBar.open("Could not verify credentials.", undefined,
          {duration: 5000}
        );
        console.error("Unsuccessful verification", err);
      }
    });

  }

  init2FA(name: string, tagId: string, token: string) {
    this.dialog.open(DrawModalComponent, {
      data: {
        "name": name,
        "token": token,
        "deviceId": tagId
      }, width: '500px', height: '600px'
    });
  }

}
