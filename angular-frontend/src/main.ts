import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';
import { datadogRum } from '@datadog/browser-rum';

import { environment } from './environments/environment';

const appVersion = environment.version;

datadogRum.init({
    applicationId: '7cf4d64a-6b98-4af2-9470-a105d4087ddb',
    clientToken: 'pub472bdbb68604d7cf6d5339900f98f7e8',
    site: 'datadoghq.eu',
    service: 'datadog-app-angular',
    env: 'production',
    version: appVersion,
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'allow'
});

window.addEventListener('error', (event) => {
    datadogRum.addError(event.error || event.message, { source: 'window' });
});

window.addEventListener('unhandledrejection', (event) => {
    datadogRum.addError(event.reason, { source: 'promise' });
});

bootstrapApplication(AppComponent, appConfig)
    .catch((err) => {
        datadogRum.addError(err, { source: 'bootstrap' });
        console.error(err);
    });

console.log(`Datadog RUM initialized with version: ${appVersion}`);
