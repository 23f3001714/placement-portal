<script setup></script>

<template>
  <div>
    <router-view />
  </div>
</template>

<style>
body {
  background-color: #121214;
  color: #e1e1e6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}

.glass-card {
  background: #202024;
  border: 1px solid #29292e;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  padding: 24px;
  margin-bottom: 24px;
}

.glass-panel {
  background: #18181b;
  border: 1px solid #27272a;
  border-radius: 8px;
  padding: 16px;
}

h1, h2, h3, h4, h5, h6 {
  color: #ffffff;
  font-weight: 600;
}

.gradient-text {
  color: #3b82f6;
}

.form-control, .form-select, textarea {
  background-color: #121214 !important;
  border: 1px solid #29292e !important;
  color: #e1e1e6 !important;
  border-radius: 6px !important;
  padding: 10px 14px !important;
}
.form-control:focus, .form-select:focus, textarea:focus {
  border-color: #3b82f6 !important;
  box-shadow: 0 0 0 0.25rem rgba(59, 130, 246, 0.25) !important;
}
.form-control::placeholder {
  color: #7c7c8a !important;
}

label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #a8a8b3;
  margin-bottom: 6px;
}

.custom-table-container {
  background: #202024;
  border: 1px solid #29292e;
  border-radius: 8px;
  overflow: hidden;
  margin-top: 16px;
  margin-bottom: 24px;
}
.table {
  color: #e1e1e6 !important;
  margin-bottom: 0 !important;
}
.table th {
  background-color: #18181b !important;
  color: #a8a8b3 !important;
  font-weight: 600 !important;
  border-bottom: 2px solid #29292e !important;
  padding: 12px 16px !important;
}
.table td {
  padding: 12px 16px !important;
  border-bottom: 1px solid #29292e !important;
  background-color: transparent !important;
}
.table tbody tr:hover {
  background-color: #18181b !important;
}

.badge-custom {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  display: inline-block;
}
.badge-applied {
  background: #2a3b5c;
  color: #a5c2f4;
}
.badge-shortlisted {
  background: #3e2b5c;
  color: #d1b8f4;
}
.badge-interview {
  background: #5c4320;
  color: #f4d1a5;
}
.badge-success {
  background: #1b4d3e;
  color: #a5f4d1;
}
.badge-danger {
  background: #5c202a;
  color: #f4a5b3;
}

.btn {
  border-radius: 6px !important;
  font-weight: 500 !important;
  padding: 8px 16px !important;
}
.btn-primary {
  background-color: #3b82f6 !important;
  border-color: #3b82f6 !important;
  color: #ffffff !important;
}
.btn-primary:hover {
  background-color: #2563eb !important;
}
.btn-success {
  background-color: #10b981 !important;
  border-color: #10b981 !important;
  color: #ffffff !important;
}
.btn-success:hover {
  background-color: #059669 !important;
}
.btn-danger {
  background-color: #ef4444 !important;
  border-color: #ef4444 !important;
  color: #ffffff !important;
}
.btn-danger:hover {
  background-color: #dc2626 !important;
}
.btn-secondary {
  background-color: #4b5563 !important;
  border-color: #4b5563 !important;
  color: #ffffff !important;
}
.btn-secondary:hover {
  background-color: #374151 !important;
}
.btn-warning {
  background-color: #f59e0b !important;
  border-color: #f59e0b !important;
  color: #ffffff !important;
}
.btn-warning:hover {
  background-color: #d97706 !important;
}

.modal {
  background-color: rgba(0, 0, 0, 0.6) !important;
}
.modal-content {
  background-color: #202024 !important;
  border: 1px solid #29292e !important;
  border-radius: 8px !important;
  color: #e1e1e6 !important;
}
.modal-header, .modal-footer {
  border-color: #29292e !important;
}
</style>
