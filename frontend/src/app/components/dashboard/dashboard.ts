import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { VehicleService } from '../../services/vehicle';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit {
  vehicles: any[] = [];
  vehicleForm: FormGroup;
  isEditing: boolean = false;
  currentVehicleId: number | null = null;

  constructor(
    private vehicleService: VehicleService,
    private fb: FormBuilder
  ) {
    this.vehicleForm = this.fb.group({
      brand: ['', Validators.required],
      model: ['', Validators.required],
      price_per_day: ['', [Validators.required, Validators.min(0)]],
      image_url: ['']
    });
  }

  ngOnInit() {
    this.loadMyVehicles();
  }

  loadMyVehicles() {
    this.vehicleService.getMyVehicles().subscribe(data => {
      this.vehicles = data;
    });
  }

  onSubmit() {
    if (this.vehicleForm.valid) {
      if (this.isEditing && this.currentVehicleId) {
        this.vehicleService.updateVehicle(this.currentVehicleId, this.vehicleForm.value).subscribe(() => {
          this.loadMyVehicles();
          this.resetForm();
        });
      } else {
        this.vehicleService.createVehicle(this.vehicleForm.value).subscribe(() => {
          this.loadMyVehicles();
          this.resetForm();
        });
      }
    }
  }

  editVehicle(vehicle: any) {
    this.isEditing = true;
    this.currentVehicleId = vehicle.id;
    this.vehicleForm.patchValue(vehicle);
  }

  deleteVehicle(id: number) {
    if (confirm('Are you sure you want to delete this vehicle?')) {
      this.vehicleService.deleteVehicle(id).subscribe(() => {
        this.loadMyVehicles();
      });
    }
  }

  resetForm() {
    this.isEditing = false;
    this.currentVehicleId = null;
    this.vehicleForm.reset();
  }
}
