"use client";

import { Group, Button, Title, Flex } from "@mantine/core";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function Header() {
  const router = useRouter();

  const onAccountClick = () => {
    router.push("/auth/login");
  };

  const onHomeClick = () => {
    router.push("/");
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

        <Button variant="transparent" color="black" size="md">
          Кошик
        </Button>

        <Button
          variant="filled"
          color="black"
          radius="8px"
          size="md"
          onClick={onAccountClick}
        >
          Мій акаунт
        </Button>
      </Group>
    </Flex>
  );
}
