import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'angular-frontend';

  constructor() {
    this.triggerError();
  }

  triggerError() {
    setTimeout(() => {
      throw new Error('🔥 Intentional test error for Datadog RUM!');
    }, 5000); // Delays 5s to ensure RUM has time to initialize
  }
}
