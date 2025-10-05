import { Group, Button, Title, Flex } from "@mantine/core";

export default function Header() {
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
      <Title order={1}>Range</Title>
      <Group gap="8px">
        <Button variant="filled" color="black" radius="8px" w="409px" size="md">
          Перейти до каталогу товарів
        </Button>

        <Button variant="transparent" color="black" size="md">
          Кошик
        </Button>
        <Button variant="filled" color="black" radius="8px" size="md">
          Мій акаунт
        </Button>
      </Group>
    </Flex>
  );
}
