import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { VehicleListComponent } from './components/vehicle-list/vehicle-list.component';
import { AuthGuard } from './guards/auth-guard';

export const routes: Routes = [
    { path: '', redirectTo: '/vehicles', pathMatch: 'full' },
    { path: 'login', component: LoginComponent },
    { path: 'register', component: RegisterComponent },
    { path: 'vehicles', component: VehicleListComponent },
    { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
    { path: '**', redirectTo: '/vehicles' }
];
