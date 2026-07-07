"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { getEmployeeById, getEmployeeSubordinates } from "@/services/hrms.service";
import type { Employee, EmployeeCardView } from "@/types/hrms.types";
import {
  EmploymentTypeLabels,
  EmploymentStatusLabels,
  GenderLabels,
  MaritalStatusLabels,
} from "@/types/hrms.types";

export default function EmployeeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const employeeId = params.id as string;

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [subordinates, setSubordinates] = useState<EmployeeCardView[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>("personal");

  useEffect(() => {
    if (employeeId) {
      loadEmployee();
      loadSubordinates();
    }
  }, [employeeId]);

  const loadEmployee = async () => {
    try {
      setLoading(true);
      const data = await getEmployeeById(Number(employeeId));
      setEmployee(data);
    } catch (error) {
      console.error("Failed to load employee:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadSubordinates = async () => {
    try {
      const data = await getEmployeeSubordinates(Number(employeeId));
      setSubordinates(data);
    } catch (error) {
      console.error("Failed to load subordinates:", error);
    }
  };

  if (loading || !employee) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading employee details...</div>
      </div>
    );
  }

  const tabs = [
    { id: "personal", label: "Personal Info" },
    { id: "employment", label: "Employment" },
    { id: "contact", label: "Contact & Address" },
    { id: "documents", label: "Documents" },
    { id: "banking", label: "Banking & Salary" },
    { id: "hierarchy", label: "Hierarchy" },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/hrms/employees")}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {employee.full_name}
              </h1>
              <p className="text-gray-600 mt-1">
                {employee.employee_code} • {employee.designation_name || "No Designation"}
              </p>
            </div>
          </div>
          <button
            onClick={() => router.push(`/hrms/employees/${employeeId}/edit`)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Edit Employee
          </button>
        </div>

        {/* Status Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Employment Status</div>
            <div className="text-lg font-semibold text-gray-900 mt-1">
              {EmploymentStatusLabels[employee.employment_status]}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Employment Type</div>
            <div className="text-lg font-semibold text-gray-900 mt-1">
              {EmploymentTypeLabels[employee.employment_type]}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Department</div>
            <div className="text-lg font-semibold text-gray-900 mt-1">
              {employee.department_name || "N/A"}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm text-gray-600">Date of Joining</div>
            <div className="text-lg font-semibold text-gray-900 mt-1">
              {new Date(employee.date_of_joining).toLocaleDateString()}
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-3 text-sm font-medium ${
                    activeTab === tab.id
                      ? "border-b-2 border-blue-600 text-blue-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Personal Info Tab */}
            {activeTab === "personal" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InfoItem label="First Name" value={employee.first_name} />
                <InfoItem label="Middle Name" value={employee.middle_name} />
                <InfoItem label="Last Name" value={employee.last_name} />
                <InfoItem label="Full Name" value={employee.full_name} />
                <InfoItem
                  label="Date of Birth"
                  value={
                    employee.date_of_birth
                      ? new Date(employee.date_of_birth).toLocaleDateString()
                      : undefined
                  }
                />
                <InfoItem label="Age" value={employee.age?.toString()} />
                <InfoItem
                  label="Gender"
                  value={employee.gender ? GenderLabels[employee.gender] : undefined}
                />
                <InfoItem label="Blood Group" value={employee.blood_group} />
                <InfoItem
                  label="Marital Status"
                  value={
                    employee.marital_status
                      ? MaritalStatusLabels[employee.marital_status]
                      : undefined
                  }
                />
                <InfoItem label="Father's Name" value={employee.father_name} />
                <InfoItem label="Mother's Name" value={employee.mother_name} />
                <InfoItem label="Spouse Name" value={employee.spouse_name} />
                <InfoItem
                  label="Number of Children"
                  value={employee.number_of_children?.toString()}
                />
              </div>
            )}

            {/* Employment Tab */}
            {activeTab === "employment" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InfoItem label="Employee Code" value={employee.employee_code} />
                <InfoItem label="Organization" value={employee.organization_name} />
                <InfoItem label="Department" value={employee.department_name} />
                <InfoItem label="Designation" value={employee.designation_name} />
                <InfoItem
                  label="Reporting Manager"
                  value={employee.reporting_manager_name}
                />
                <InfoItem
                  label="Employment Type"
                  value={EmploymentTypeLabels[employee.employment_type]}
                />
                <InfoItem
                  label="Employment Status"
                  value={EmploymentStatusLabels[employee.employment_status]}
                />
                <InfoItem
                  label="Date of Joining"
                  value={new Date(employee.date_of_joining).toLocaleDateString()}
                />
                <InfoItem
                  label="Date of Confirmation"
                  value={
                    employee.date_of_confirmation
                      ? new Date(employee.date_of_confirmation).toLocaleDateString()
                      : undefined
                  }
                />
                <InfoItem label="Work Location" value={employee.work_location} />
                <InfoItem label="Shift Type" value={employee.shift_type} />
                <InfoItem
                  label="On Probation"
                  value={employee.is_on_probation ? "Yes" : "No"}
                />
                <InfoItem
                  label="Probation End Date"
                  value={
                    employee.probation_end_date
                      ? new Date(employee.probation_end_date).toLocaleDateString()
                      : undefined
                  }
                />
                <InfoItem
                  label="Notice Period"
                  value={
                    employee.notice_period_days
                      ? `${employee.notice_period_days} days`
                      : undefined
                  }
                />
              </div>
            )}

            {/* Contact & Address Tab */}
            {activeTab === "contact" && (
              <div className="space-y-8">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Contact Information
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InfoItem label="Personal Email" value={employee.personal_email} />
                    <InfoItem label="Official Email" value={employee.official_email} />
                    <InfoItem label="Mobile" value={employee.mobile} />
                    <InfoItem label="Alternate Mobile" value={employee.alternate_mobile} />
                    <InfoItem
                      label="Emergency Contact Name"
                      value={employee.emergency_contact_name}
                    />
                    <InfoItem
                      label="Emergency Contact Number"
                      value={employee.emergency_contact_number}
                    />
                    <InfoItem
                      label="Emergency Contact Relation"
                      value={employee.emergency_contact_relation}
                    />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Current Address
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InfoItem
                      label="Address Line 1"
                      value={employee.current_address_line1}
                    />
                    <InfoItem
                      label="Address Line 2"
                      value={employee.current_address_line2}
                    />
                    <InfoItem label="City" value={employee.current_city} />
                    <InfoItem label="State" value={employee.current_state} />
                    <InfoItem label="Pincode" value={employee.current_pincode} />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Permanent Address
                  </h3>
                  {employee.is_permanent_same_as_current ? (
                    <p className="text-gray-600">Same as current address</p>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <InfoItem
                        label="Address Line 1"
                        value={employee.permanent_address_line1}
                      />
                      <InfoItem
                        label="Address Line 2"
                        value={employee.permanent_address_line2}
                      />
                      <InfoItem label="City" value={employee.permanent_city} />
                      <InfoItem label="State" value={employee.permanent_state} />
                      <InfoItem label="Pincode" value={employee.permanent_pincode} />
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Documents Tab */}
            {activeTab === "documents" && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <InfoItem label="PAN Number" value={employee.pan_number} />
                <InfoItem label="Aadhaar Number" value={employee.aadhaar_number} />
                <InfoItem label="Passport Number" value={employee.passport_number} />
                <InfoItem
                  label="Driving License"
                  value={employee.driving_license_number}
                />
                <InfoItem
                  label="Highest Qualification"
                  value={employee.highest_qualification}
                />
                <InfoItem label="Specialization" value={employee.specialization} />
                <InfoItem label="University" value={employee.university} />
                <InfoItem
                  label="Year of Passing"
                  value={employee.year_of_passing?.toString()}
                />
                <InfoItem
                  label="Total Experience"
                  value={
                    employee.total_experience_years
                      ? `${employee.total_experience_years} years`
                      : undefined
                  }
                />
              </div>
            )}

            {/* Banking & Salary Tab */}
            {activeTab === "banking" && (
              <div className="space-y-8">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Salary Account
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InfoItem label="Bank Name" value={employee.salary_bank_name} />
                    <InfoItem
                      label="Account Number"
                      value={employee.salary_account_number}
                    />
                    <InfoItem label="IFSC Code" value={employee.salary_ifsc_code} />
                    <InfoItem label="PF Number" value={employee.pf_number} />
                    <InfoItem label="UAN Number" value={employee.uan_number} />
                    <InfoItem label="ESI Number" value={employee.esi_number} />
                  </div>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Salary Details
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <InfoItem
                      label="Current CTC"
                      value={
                        employee.current_ctc
                          ? `₹${employee.current_ctc.toLocaleString()}`
                          : undefined
                      }
                    />
                    <InfoItem
                      label="Basic Salary"
                      value={
                        employee.basic_salary
                          ? `₹${employee.basic_salary.toLocaleString()}`
                          : undefined
                      }
                    />
                    <InfoItem
                      label="Gross Salary"
                      value={
                        employee.gross_salary
                          ? `₹${employee.gross_salary.toLocaleString()}`
                          : undefined
                      }
                    />
                    <InfoItem
                      label="Net Salary"
                      value={
                        employee.net_salary
                          ? `₹${employee.net_salary.toLocaleString()}`
                          : undefined
                      }
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Hierarchy Tab */}
            {activeTab === "hierarchy" && (
              <div className="space-y-6">
                {employee.reporting_manager_name && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Reports To
                    </h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="font-medium text-gray-900">
                        {employee.reporting_manager_name}
                      </div>
                    </div>
                  </div>
                )}

                {subordinates.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Direct Subordinates ({subordinates.length})
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {subordinates.map((subordinate) => (
                        <div
                          key={subordinate.id}
                          className="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100"
                          onClick={() =>
                            router.push(`/hrms/employees/${subordinate.id}`)
                          }
                        >
                          <div className="font-medium text-gray-900">
                            {subordinate.full_name}
                          </div>
                          <div className="text-sm text-gray-600">
                            {subordinate.employee_code}
                          </div>
                          <div className="text-sm text-gray-600">
                            {subordinate.designation_name}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoItem({
  label,
  value,
}: {
  label: string;
  value?: string | null;
}) {
  return (
    <div>
      <div className="text-sm text-gray-600">{label}</div>
      <div className="text-base text-gray-900 mt-1">{value || "-"}</div>
    </div>
  );
}
