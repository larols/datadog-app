import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataService } from '../data.service';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  viewsData: any = {}; 
  uidData: any = {};
  quoteData: any = {};
  staticText: string = "Welcome to the Home Page! This is a simple Angular application that fetches dynamic data.";

  constructor(private dataService: DataService) { }

  ngOnInit(): void {
    this.dataService.getViews().subscribe({
      next: data => this.viewsData = data,
      error: () => {
        console.error('API call failed for viewsData');
        throw new Error('API call failed in HomeComponent!');
      }
    });

    this.dataService.getUidLatest().subscribe({
      next: data => this.uidData = data,
      error: () => {
        console.error('UID API call failed');
        throw new Error('UID API call failed in HomeComponent!');
      }
    });

    this.dataService.getQuotesRandom().subscribe({
      next: data => this.quoteData = data,
      error: () => {
        console.error('Quotes API call failed');
        throw new Error('Quotes API call failed in HomeComponent!');
      }
    });


    setTimeout(() => {
      console.error('Intentional error in HomeComponent!');
      throw new Error('Intentional test error for Datadog RUM!');
    }, 3000);
  }


  generateError(): void {
    console.error('User clicked error button in HomeComponent!');
    throw new Error('User-triggered test error for Datadog RUM!');
  }
}
