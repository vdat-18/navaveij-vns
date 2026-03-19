"use client";

import React from "react";
import { RbacRole } from "@/types/access-monitoring";

interface RoleManagementTabProps {
  roles: RbacRole[];
}

export function RoleManagementTab({ roles }: RoleManagementTabProps) {
  const resourceKeys = Array.from(new Set(roles.flatMap((role) => Object.keys(role.permissions))));

  return (
    <div className="navavej-card p-6 overflow-auto">
      <h3 className="text-sm font-black uppercase tracking-widest text-navavej-gray-dark mb-4">Role Management</h3>
      <table className="w-full text-left min-w-[700px]">
        <thead>
          <tr className="bg-navavej-gray-light/40">
            <th className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">Role</th>
            {resourceKeys.map((resource) => (
              <th key={resource} className="px-3 py-2 text-[10px] font-black uppercase tracking-widest">{resource}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {roles.map((role) => (
            <tr key={role.role_id} className="border-t border-navavej-border">
              <td className="px-3 py-2 text-xs font-black">{role.label}</td>
              {resourceKeys.map((resource) => (
                <td key={`${role.role_id}-${resource}`} className="px-3 py-2 text-xs font-bold">
                  {(role.permissions[resource] || []).join(", ") || "—"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
