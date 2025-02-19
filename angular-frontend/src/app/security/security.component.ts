import { Component } from '@angular/core';
import { DataService } from '../data.service';

@Component({
  selector: 'app-security',
  templateUrl: './security.component.html',
  styleUrls: ['./security.component.css']
})
export class SecurityComponent {
  ssrfUrl = '';
  ssrfResponse: any;
  deserializePayload = '';
  deserializeResponse: any;

  constructor(private dataService: DataService) { }

  testSsrf(): void {
    this.dataService.postSsrf(this.ssrfUrl).subscribe(response => {
      this.ssrfResponse = response;
    });
  }

  testDeserialize(): void {
    this.dataService.postDeserialize(this.deserializePayload).subscribe(response => {
      this.deserializeResponse = response;
    });
  }
}