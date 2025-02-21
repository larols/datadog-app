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
    this.dataService.getViews().subscribe(data => this.viewsData = data);
    this.dataService.getUidLatest().subscribe(data => this.uidData = data);
    this.dataService.getQuotesRandom().subscribe(data => this.quoteData = data);
  }
}
