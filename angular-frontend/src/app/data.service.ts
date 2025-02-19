import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class DataService {
  private apiUrl = '/api'; // Adjust if your API base URL is different

  constructor(private http: HttpClient) { }

  getViews(): Observable<any> {
    return this.http.get(`${this.apiUrl}/views`);
  }

  getUidLatest(): Observable<any> {
    return this.http.get(`${this.apiUrl}/uid/latest`);
  }

  getQuotesRandom(): Observable<any> {
    return this.http.get(`${this.apiUrl}/quotes/random`);
  }

  postSsrf(url: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/uid/ssrf`, { url });
  }

  postDeserialize(payload: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/deserialize`, { py: payload });
  }
}