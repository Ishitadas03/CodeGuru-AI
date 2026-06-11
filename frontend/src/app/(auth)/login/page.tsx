"use client";

import React from "react";
import LoginForm from "@/features/auth/LoginForm";
import OAuthButtons from "@/features/auth/OAuthButtons";

export default function LoginPage() {
  return (
    <div className="space-y-6">
      <LoginForm />
      <OAuthButtons />
    </div>
  );
}
