import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';
import { datadogRum } from '@datadog/browser-rum';

// ✅ Initialize Datadog RUM before bootstrapping Angular
datadogRum.init({
    applicationId: '7cf4d64a-6b98-4af2-9470-a105d4087ddb',
    clientToken: 'pub472bdbb68604d7cf6d5339900f98f7e8',
    site: 'datadoghq.eu',
    service: 'datadog-app-angular',
    env: 'production', // Change dynamically if needed
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    defaultPrivacyLevel: 'allow',
});

// ✅ Ensure RUM starts collecting session data
datadogRum.startSessionReplayRecording();

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
