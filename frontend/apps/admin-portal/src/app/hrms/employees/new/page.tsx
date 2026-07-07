"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createEmployee } from "@/services/hrms.service";
import { getActiveOrganizations } from "@/services/hrms.service";
import { getDepartments } from "@/services/hrms.service";
import { getDesignations } from "@/services/hrms.service";
import type {
  EmployeeCreate,
  OrganizationListItem,
  DepartmentListItem,
  DesignationListItem,
  EmploymentType,
  Gender,
  BloodGroup,
  MaritalStatus,
} from "@/types/hrms.types";
import {
  EmploymentTypeLabels,
  GenderLabels,
  MaritalStatusLabels,
} from "@/types/hrms.types";

export default function NewEmployeePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [organizations, setOrganizations] = useState<OrganizationListItem[]>([]);
  const [departments, setDepartments] = useState<DepartmentListItem[]>([]);
  const [designations, setDesignations] = useState<DesignationListItem[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);

  const [formData, setFormData] = useState<EmployeeCreate>({
    organization_id: 0,
    employment_type: "permanent" as EmploymentType,
    date_of_joining: new Date().toISOString().split("T")[0],
    first_name: "",
    last_name: "",
    mobile: "",
    is_active: true,
    notice_period_days: 30,
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    loadDropdownData();
  }, []);

  const loadDropdownData = async () => {
    try {
      const [orgs, depts, desigs] = await Promise.all([
        getActiveOrganizations(),
        getDepartments({ is_active: true, page_size: 100 }),
        getDesignations({ is_active: true, page_size: 100 }),
      ]);
      setOrganizations(orgs);
      setDepartments(depts.items);
      setDesignations(desigs.items);
    } catch (error) {
      console.error("Failed to load dropdown data:", error);
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.organization_id) newErrors.organization_id = "Organization is required";
    if (!formData.first_name) newErrors.first_name = "First name is required";
    if (!formData.last_name) newErrors.last_name = "Last name is required";
    if (!formData.mobile) newErrors.mobile = "Mobile is required";
    else if (formData.mobile.length !== 10) newErrors.mobile = "Mobile must be 10 digits";
    if (!formData.date_of_joining) newErrors.date_of_joining = "Joining date is required";

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      alert("Please fix the errors in the form");
      return;
    }

    setLoading(true);
    try {
      await createEmployee(formData);
      alert("Employee created successfully!");
      router.push("/hrms/employees");
    } catch (error: any) {
      console.error("Failed to create employee:", error);
      alert(error.response?.data?.detail || "Failed to create employee");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    field: keyof EmployeeCreate,
    value: any
  ) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Add New Employee</h1>
            <p className="text-gray-600 mt-1">Create a new employee record</p>
          </div>
          <button
            onClick={() => router.push("/hrms/employees")}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to List
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow">
          {/* Organization & Employment */}
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Organization & Employment
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label="Organization *" error={errors.organization_id}>
                <select
                  value={formData.organization_id || ""}
                  onChange={(e) =>
                    handleInputChange("organization_id", Number(e.target.value))
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select Organization</option>
                  {organizations.map((org) => (
                    <option key={org.id} value={org.id}>
                      {org.organization_name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Department">
                <select
                  value={formData.department_id || ""}
                  onChange={(e) =>
                    handleInputChange("department_id", Number(e.target.value) || undefined)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Department</option>
                  {departments.map((dept) => (
                    <option key={dept.id} value={dept.id}>
                      {dept.department_name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Designation">
                <select
                  value={formData.designation_id || ""}
                  onChange={(e) =>
                    handleInputChange("designation_id", Number(e.target.value) || undefined)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Designation</option>
                  {designations.map((desig) => (
                    <option key={desig.id} value={desig.id}>
                      {desig.designation_name}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Employment Type *">
                <select
                  value={formData.employment_type}
                  onChange={(e) =>
                    handleInputChange("employment_type", e.target.value as EmploymentType)
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  {Object.entries(EmploymentTypeLabels).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Date of Joining *" error={errors.date_of_joining}>
                <input
                  type="date"
                  value={formData.date_of_joining}
                  onChange={(e) => handleInputChange("date_of_joining", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </FormField>

              <FormField label="Date of Confirmation">
                <input
                  type="date"
                  value={formData.date_of_confirmation || ""}
                  onChange={(e) => handleInputChange("date_of_confirmation", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FormField>
            </div>
          </div>

          {/* Personal Information */}
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Personal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label="First Name *" error={errors.first_name}>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange("first_name", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </FormField>

              <FormField label="Middle Name">
                <input
                  type="text"
                  value={formData.middle_name || ""}
                  onChange={(e) => handleInputChange("middle_name", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FormField>

              <FormField label="Last Name *" error={errors.last_name}>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange("last_name", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </FormField>

              <FormField label="Date of Birth">
                <input
                  type="date"
                  value={formData.date_of_birth || ""}
                  onChange={(e) => handleInputChange("date_of_birth", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FormField>

              <FormField label="Gender">
                <select
                  value={formData.gender || ""}
                  onChange={(e) => handleInputChange("gender", (e.target.value as Gender) || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Gender</option>
                  {Object.entries(GenderLabels).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Blood Group">
                <select
                  value={formData.blood_group || ""}
                  onChange={(e) => handleInputChange("blood_group", (e.target.value as BloodGroup) || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Blood Group</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </FormField>

              <FormField label="Marital Status">
                <select
                  value={formData.marital_status || ""}
                  onChange={(e) => handleInputChange("marital_status", (e.target.value as MaritalStatus) || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Marital Status</option>
                  {Object.entries(MaritalStatusLabels).map(([key, label]) => (
                    <option key={key} value={key}>
                      {label}
                    </option>
                  ))}
                </select>
              </FormField>

              <FormField label="Father's Name">
                <input
                  type="text"
                  value={formData.father_name || ""}
                  onChange={(e) => handleInputChange("father_name", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FormField>
            </div>
          </div>

          {/* Contact Information */}
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Contact Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label="Mobile *" error={errors.mobile}>
                <input
                  type="tel"
                  value={formData.mobile}
                  onChange={(e) => handleInputChange("mobile", e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="10 digit mobile number"
                  maxLength={10}
                  required
                />
              </FormField>

              <FormField label="Personal Email">
                <input
                  type="email"
                  value={formData.personal_email || ""}
                  onChange={(e) => handleInputChange("personal_email", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FormField>

              <FormField label="Official Email">
                <input
                  type="email"
                  value={formData.official_email || ""}
                  onChange={(e) => handleInputChange("official_email", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </FormField>

              <FormField label="Emergency Contact Number">
                <input
                  type="tel"
                  value={formData.emergency_contact_number || ""}
                  onChange={(e) => handleInputChange("emergency_contact_number", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  maxLength={10}
                />
              </FormField>
            </div>
          </div>

          {/* Identity Documents */}
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Identity Documents
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label="PAN Number">
                <input
                  type="text"
                  value={formData.pan_number || ""}
                  onChange={(e) => handleInputChange("pan_number", e.target.value.toUpperCase() || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="ABCDE1234F"
                  maxLength={10}
                />
              </FormField>

              <FormField label="Aadhaar Number">
                <input
                  type="text"
                  value={formData.aadhaar_number || ""}
                  onChange={(e) => handleInputChange("aadhaar_number", e.target.value || undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="12 digit Aadhaar"
                  maxLength={12}
                />
              </FormField>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="p-6 flex justify-end gap-4">
            <button
              type="button"
              onClick={() => router.push("/hrms/employees")}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? "Creating..." : "Create Employee"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function FormField({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      {children}
      {error && <p className="text-sm text-red-600 mt-1">{error}</p>}
    </div>
  );
}
