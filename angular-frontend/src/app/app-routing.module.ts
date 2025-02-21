import { Routes, provideRouter } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { AboutComponent } from './about/about.component';
import { SecurityComponent } from './security/security.component';

export const routes: Routes = [
  { path: '', redirectTo: '/home', pathMatch: 'full' }, // Redirect to /home by default
  { path: 'home', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'security', component: SecurityComponent }
];

export const appRouting = provideRouter(routes);
