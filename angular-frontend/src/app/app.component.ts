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
      // Throwing error in global scope (Datadog can now capture it)
      window.onerror?.('Intentional load error for Datadog RUM!', '', 0, 0, new Error('Intentional test error for Datadog RUM!'));
    }, 5000); // Delays to ensure RUM is initialized
  }
}
