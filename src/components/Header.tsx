"use client";

import { Group, Button, Title, Flex } from "@mantine/core";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext"; // ⚠️ важливо!

export default function Header() {
  const router = useRouter();
  const { user } = useAuth(); // <-- тут беремо користувача

  const onAccountClick = () => {
    if (user) {
      router.push("/profile"); // якщо користувач увійшов
    } else {
      router.push("/auth/login"); // якщо не увійшов
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
    </Flex>
  );
}
