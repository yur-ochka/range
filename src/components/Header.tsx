"use client";

import { Group, Button, Title, Flex } from "@mantine/core";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useState, useEffect } from "react";
import { UserModal } from "@/components/UserModal";

export default function Header() {
  const router = useRouter();
  const { user } = useAuth();

  const [opened, setOpened] = useState(false);
  const [isLogged, setIsLogged] = useState(false);

  useEffect(() => {
    setIsLogged(!!localStorage.getItem("access_token"));
  }, []);

  const onAccountClick = () => {
    if (user) {
      setOpened(true);
    } else {
      router.push("/auth/login");
    }
  };

  const onHomeClick = () => {
    router.push("/");
  };

  const onCartClick = () => {
    router.push("/cart");
  };

  return (
    <Flex
      justify="space-between"
      align="center"
      w="100%"
      p="md"
      pl="80px"
      pr="80px"
      h="164px"
    >
      <Link onClick={onHomeClick} href="/" style={{ textDecoration: "none" }}>
        <Title order={1}>Range</Title>
      </Link>

      <Group gap="8px">
        <Button variant="filled" color="black" radius="8px" w="409px" size="md">
          Перейти до каталогу товарів
        </Button>

        <Button
          onClick={onCartClick}
          variant="transparent"
          color="black"
          size="md"
        >
          Кошик
        </Button>

        <Button
          variant="filled"
          color="black"
          radius="8px"
          size="md"
          onClick={onAccountClick}
        >
          {user ? "Мій акаунт" : "Вхід / Реєстрація"}
        </Button>
      </Group>
      <UserModal opened={opened} onClose={() => setOpened(false)} />
    </Flex>
  );
}
