"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { Users, Plus, Edit2, Trash2, Phone, Heart, AlertCircle } from "lucide-react";
import CustomerFamilyModal from "@/components/CustomerFamilyModal";

interface FamilyMember {
  id: number;
  customer_id: number;
  relationship_type_id: number;
  relationship_name?: string;
  name: string;
  date_of_birth?: string;
  age?: number;
  gender?: string;
  mobile?: string;
  occupation?: string;
  monthly_income?: number;
  is_dependent: boolean;
  is_emergency_contact: boolean;
  is_nominee: boolean;
  nominee_percentage?: number;
  created_at: string;
}

interface RelationshipType {
  id: number;
  name: string;
  code: string;
}

export default function CustomerFamilyPage() {
  const params = useParams();
  const customerId = params?.id as string;

  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([]);
  const [relationships, setRelationships] = useState<RelationshipType[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<FamilyMember | undefined>();
  const [nomineeValidation, setNomineeValidation] = useState<{ valid: boolean; total: number }>({
    valid: true,
    total: 0
  });

  useEffect(() => {
    if (customerId) {
      fetchFamilyMembers();
      fetchRelationships();
    }
  }, [customerId]);

  useEffect(() => {
    validateNominees();
  }, [familyMembers]);

  const fetchFamilyMembers = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/customers/${customerId}/family`, {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setFamilyMembers(data);
      }
    } catch (error) {
      console.error("Error fetching family members:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRelationships = async () => {
    try {
      const response = await fetch("/api/v1/masterdata/relationship-types", {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setRelationships(data.items || data);
      }
    } catch (error) {
      console.error("Error fetching relationships:", error);
    }
  };

  const validateNominees = async () => {
    try {
      const response = await fetch(`/api/v1/customers/${customerId}/family/validate-nominees`, {
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        const data = await response.json();
        setNomineeValidation(data);
      }
    } catch (error) {
      console.error("Error validating nominees:", error);
    }
  };

  const handleSave = async (data: any) => {
    try {
      const url = editingMember
        ? `/api/v1/customers/${customerId}/family/${editingMember.id}`
        : `/api/v1/customers/${customerId}/family`;

      const method = editingMember ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Failed to save");
      }

      await fetchFamilyMembers();
      setIsModalOpen(false);
      setEditingMember(undefined);
    } catch (error) {
      throw error;
    }
  };

  const handleEdit = (member: FamilyMember) => {
    setEditingMember(member);
    setIsModalOpen(true);
  };

  const handleDelete = async (memberId: number) => {
    if (!confirm("Are you sure you want to delete this family member?")) return;

    try {
      const response = await fetch(`/api/v1/customers/${customerId}/family/${memberId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" }
      });

      if (response.ok) {
        await fetchFamilyMembers();
      } else {
        alert("Failed to delete family member");
      }
    } catch (error) {
      console.error("Error deleting family member:", error);
      alert("Failed to delete family member");
    }
  };

  const handleAddNew = () => {
    setEditingMember(undefined);
    setIsModalOpen(true);
  };

  const nominees = familyMembers.filter(m => m.is_nominee);
  const emergencyContacts = familyMembers.filter(m => m.is_emergency_contact);
  const dependents = familyMembers.filter(m => m.is_dependent);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Family Members</h2>
          <p className="text-sm text-gray-600 mt-1">
            Manage customer's family members, nominees, and emergency contacts
          </p>
        </div>
        <button
          onClick={handleAddNew}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4" />
          Add Family Member
        </button>
      </div>

      {/* Nominee Validation Alert */}
      {nominees.length > 0 && !nomineeValidation.valid && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-semibold text-red-900">
                Nominee Percentage Invalid
              </h4>
              <p className="text-sm text-red-700 mt-1">
                Total nominee percentage is {nomineeValidation.total}%. It must equal exactly 100%.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Members</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{familyMembers.length}</p>
            </div>
            <Users className="w-8 h-8 text-blue-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Nominees</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{nominees.length}</p>
            </div>
            <Heart className="w-8 h-8 text-red-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Emergency Contacts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{emergencyContacts.length}</p>
            </div>
            <Phone className="w-8 h-8 text-orange-600 opacity-20" />
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Dependents</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{dependents.length}</p>
            </div>
            <Users className="w-8 h-8 text-purple-600 opacity-20" />
          </div>
        </div>
      </div>

      {/* Family Members Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Member
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Relationship
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Occupation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Roles
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {familyMembers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-sm text-gray-600 mb-4">No family members added yet</p>
                    <button
                      onClick={handleAddNew}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Add your first family member
                    </button>
                  </td>
                </tr>
              ) : (
                familyMembers.map((member) => (
                  <tr key={member.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{member.name}</div>
                        {member.age && (
                          <div className="text-sm text-gray-500">
                            {member.age} years • {member.gender ? member.gender.charAt(0).toUpperCase() + member.gender.slice(1) : ''}
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">{member.relationship_name || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {member.mobile ? (
                        <div className="text-sm text-gray-900">{member.mobile}</div>
                      ) : (
                        <span className="text-sm text-gray-400">No contact</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm">
                        <div className="text-gray-900">{member.occupation || 'N/A'}</div>
                        {member.monthly_income && (
                          <div className="text-gray-500">₹{member.monthly_income.toLocaleString('en-IN')}/mo</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap gap-1">
                        {member.is_nominee && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <Heart className="w-3 h-3 mr-1" />
                            Nominee {member.nominee_percentage ? `(${member.nominee_percentage}%)` : ''}
                          </span>
                        )}
                        {member.is_emergency_contact && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            <Phone className="w-3 h-3 mr-1" />
                            Emergency
                          </span>
                        )}
                        {member.is_dependent && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                            Dependent
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleEdit(member)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(member.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal */}
      <CustomerFamilyModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingMember(undefined);
        }}
        onSave={handleSave}
        member={editingMember}
        relationships={relationships}
      />
    </div>
  );
}
