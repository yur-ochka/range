"use client";

import { useEffect, useState } from "react";
import { UserModal } from "@/components/UserModal";

export default function UserPage() {
  const [opened, setOpened] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      setOpened(true);
    } else {
      alert("Ви не авторизовані!");
    }
  }, []);

  return <UserModal opened={opened} onClose={() => setOpened(false)} />;
}
