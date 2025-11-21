import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth';

@Injectable({
  providedIn: 'root'
})
export class VehicleService {
  private apiUrl = 'http://localhost:8000/vehicles';

  constructor(private http: HttpClient, private authService: AuthService) { }

  private getHeaders(): HttpHeaders {
    const token = this.authService.getToken();
    return new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });
  }

  getVehicles(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl);
  }

  getMyVehicles(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/my-vehicles`, { headers: this.getHeaders() });
  }

  createVehicle(vehicle: any): Observable<any> {
    return this.http.post(this.apiUrl, vehicle, { headers: this.getHeaders() });
  }

  updateVehicle(id: number, vehicle: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, vehicle, { headers: this.getHeaders() });
  }

  deleteVehicle(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`, { headers: this.getHeaders() });
  }
}
