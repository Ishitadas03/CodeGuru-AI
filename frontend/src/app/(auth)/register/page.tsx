"use client";

import React from "react";
import RegisterForm from "@/features/auth/RegisterForm";
import OAuthButtons from "@/features/auth/OAuthButtons";

export default function RegisterPage() {
  return (
    <div className="space-y-6">
      <RegisterForm />
      <OAuthButtons />
    </div>
  );
}
