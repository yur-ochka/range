import { Box, Image, Stack, Text, Title } from "@mantine/core";
import Link from "next/link";

export interface ItemCardProps {
  title: string;
  price: number;
  imageUrl: string;
  altText?: string;
  id: string;
}

export function ItemCard({
  title,
  price,
  imageUrl,
  altText,
  id,
}: ItemCardProps) {
  return (
    <Link href={`/item/${id}`} style={{ textDecoration: "none" }}>
      <Box mah="489px">
        <Stack align="stretch" gap="sm">
          <Image src={imageUrl} alt={altText ? altText : "Placeholder"}></Image>
          <Title order={4}>{title}</Title>
          <Text>{price}₴</Text>
        </Stack>
      </Box>
    </Link>
  );
}
