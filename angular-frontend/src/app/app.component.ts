import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Angular App';

  constructor() {
    this.triggerError(); // Call error function on load
  }

  triggerError() {
    setTimeout(() => {
      throw new Error('🔥 Intentional test error for Datadog!');
    }, 3000); // Delay to ensure Datadog RUM captures it
  }
}
