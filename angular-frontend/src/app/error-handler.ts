import { ErrorHandler, Injectable } from '@angular/core';
import { datadogRum } from '@datadog/browser-rum';

@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
  handleError(error: any) {
    console.error('🔥 Global Error Captured:', error);
    datadogRum.addError(error, { source: 'angular-global' }); // ✅ Send error to Datadog
    throw error; // Rethrow to avoid suppression
  }
}
