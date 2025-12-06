import { Box, Image, Stack, Text, Title } from "@mantine/core";
import Link from "next/link";

export interface ItemCardProps {
  title: string;
  price: number;
  image_url: string;
  altText?: string;
  id: string;
}

export function ItemCard({
  title,
  price,
  image_url,
  altText,
  id,
}: ItemCardProps) {
  return (
    <Link href={`/item/${id}`} style={{ textDecoration: "none" }}>
      <Box mah="489px">
        <Stack align="stretch" gap="sm" justify="space-between">
          <Image
            src={image_url}
            fit="contain"
            alt={altText ? altText : "Placeholder"}
            className="object-cover w-full h-60"
          ></Image>
          <Title order={4}>{title}</Title>
          <Text>{price}₴</Text>
        </Stack>
      </Box>
    </Link>
  );
}
