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
  viewsData: any;
  uidData: any;
  quoteData: any;
  staticText: string = "Welcome to the Home Page! This is a simple Angular application that fetches dynamic data.";

  constructor(private dataService: DataService) { }

  ngOnInit(): void {
    
    setTimeout(() => {
      throw new Error('Intentional error in HomeComponent for Datadog RUM!');
    }, 3000);

    this.dataService.getViews().subscribe({
      next: data => this.viewsData = data,
      error: () => {
        throw new Error('API call failed in HomeComponent!');
      }
    });

    this.dataService.getUidLatest().subscribe({
      next: data => this.uidData = data,
      error: () => {
        throw new Error('UID API call failed in HomeComponent!');
      }
    });

    this.dataService.getQuotesRandom().subscribe({
      next: data => this.quoteData = data,
      error: () => {
        throw new Error('uotes API call failed in HomeComponent!');
      }
    });
  }


  generateError() {
    throw new Error('User clicked the error button in HomeComponent!');
  }
}
