"use client";

import { useEffect, useState } from "react";
import { Modal, Text } from "@mantine/core";

export function UserModal({
  opened,
  onClose,
}: {
  opened: boolean;
  onClose: () => void;
}) {
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    const storedUser = localStorage.getItem("username");
    if (storedUser) setUsername(storedUser);
    console.log(localStorage);
  }, []);

  return (
    <Modal opened={opened} onClose={onClose} title="Ваш профіль">
      <Text size="lg" mb="md">
        Вітаю! Ви увійшли в акаунт.
      </Text>

      <Text>
        Ваш логін: <b>{username ?? "Невідомо"}</b>
      </Text>
    </Modal>
  );
}
