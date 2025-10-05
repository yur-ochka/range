import { Box, SimpleGrid } from "@mantine/core";
import { CategoryCardProps } from "./CategoryCard";
import { CategoryCard } from "./CategoryCard";
interface CategoryListProps {
  categories: CategoryCardProps[];
}
export function CategoryList({ categories }: CategoryListProps) {
  return (
    <Box>
      <SimpleGrid cols={4}>
        {categories.map((category) => (
          <CategoryCard {...category} key={category.id}></CategoryCard>
        ))}
      </SimpleGrid>
    </Box>
  );
}
