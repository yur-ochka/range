import { Box, Image, Stack, Text, Title } from "@mantine/core";
import Link from "next/link";
import { ItemCardProps } from "../category";

export interface CategoryCardProps {
  title: string;
  description: string | null;
  image_url: string;
  altText?: string;
  id: string;
  products: ItemCardProps[];
}

export function CategoryCard({
  title,
  description,
  image_url,
  altText,
  id,
}: CategoryCardProps) {
  return (
    <Link href={`/category/${id}`} style={{ textDecoration: "none" }}>
      <Box h={500} className="flex flex-col justify-between">
        <Stack h={500} align="stretch" gap="sm" justify="space-between">
          <Image
            src={image_url}
            fit="contain"
            alt={altText ? altText : "Placeholder"}
            className="object-cover w-full h-96"
          ></Image>
          <Title order={4}>{title}</Title>
          <Text>{description}</Text>
        </Stack>
      </Box>
    </Link>
  );
}
