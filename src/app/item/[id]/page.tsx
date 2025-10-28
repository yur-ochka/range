import {
  Box,
  Group,
  Image,
  Stack,
  Title,
  Text,
  Rating,
  Button,
  Center,
  Flex,
} from "@mantine/core";

const item = {
  id: "1",
  title: "iPhone 17 Pro Max 256 GB Cosmic Orange",
  subtitile: "Short subtitle here",
  description: "This is a detailed description of the item.",
  inStock: true,
  price: 149.99,
  imageUrl: "https://s.ek.ua/jpg_zoom1/2827844.jpg",
  altText: "Sample Item Image",
  rating: 4.5,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
};
export interface ItemProps {
  id: string;
  title: string;
  subtitile: string | null;
  description: string | null;
  inStock?: boolean;
  price: number;
  imageUrl: string | null;
  altText?: string;
  rating?: number;
  createdAt: string;
  updatedAt: string;
}
export default function ItemPage({
  id,
  title,
  subtitile,
  description,
  inStock,
  price,
  imageUrl,
  altText,
  createdAt,
  updatedAt,
}: ItemProps) {
  return (
    <Center py="xl">
      <Box w="90%" maw={1200}>
        <Group align="flex-start" wrap="nowrap">
          <Image
            src={item.imageUrl}
            alt={item.altText ?? ""}
            fit="contain"
            mah={600}
            maw={500}
            style={{ flexShrink: 0 }}
          />

          <Stack h={600} justify="space-between" p="lg" style={{ flex: 1 }}>
            <Stack gap="md">
              <Title order={1} style={{ lineHeight: 1.15 }}>
                {item.title}
              </Title>

              <Text c={item.inStock ? "green" : "red"}>
                {item.inStock ? "В наявності" : "Немає в наявності"}
              </Text>

              <Title order={2}>{item.price} грн</Title>

              <div>
                <Text fw={600} mb={4}>
                  Рейтинг товару:
                </Text>
                <Rating
                  value={item.rating}
                  fractions={10}
                  readOnly
                  size="lg"
                  color="orange"
                />
              </div>
            </Stack>

            <Stack gap="md">
              <Group gap="md">
                <Button variant="filled" color="black" radius="md">
                  Додати до кошика
                </Button>
                <Button variant="outline" color="dark" radius="md">
                  Оформити замовлення
                </Button>
              </Group>
            </Stack>
          </Stack>
        </Group>
      </Box>
    </Center>
  );
}
