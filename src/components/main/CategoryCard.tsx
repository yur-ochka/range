import { Box, Image, Stack, Text, Title } from "@mantine/core";
import Link from "next/link";

export interface CategoryCardProps {
  title: string;
  description: string | null;
  imageUrl: string;
  altText?: string;
  id: string;
}

export function CategoryCard({
  title,
  description,
  imageUrl,
  altText,
  id,
}: CategoryCardProps) {
  return (
    <Link href={`/category/${id}`} style={{ textDecoration: "none" }}>
      <Box mah="489px">
        <Stack align="stretch" gap="sm">
          <Image src={imageUrl} alt={altText ? altText : "Placeholder"}></Image>
          <Title order={4}>{title}</Title>
          <Text>{description}</Text>
        </Stack>
      </Box>
    </Link>
  );
}
