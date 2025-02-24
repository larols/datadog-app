import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  staticText: string = "Welcome to the Home Page!";

  constructor() {}

  ngOnInit(): void {
    // Throws an error immediately when the page loads
    setTimeout(() => {
      console.error('🔥 Intentional error in HomeComponent!'); // Logs in the browser console
      throw new Error('🔥 Intentional test error for Datadog RUM!');
    }, 3000); // Delayed to ensure RUM is initialized
  }
}

generateError() {
  console.error('🔥 User clicked error button in HomeComponent!'); // Console log for debugging
  throw new Error('🔥 User-triggered test error for Datadog RUM!');
}

