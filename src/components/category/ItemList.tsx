import { Box, SimpleGrid } from "@mantine/core";
import { ItemCardProps } from "./ItemCard";
import { ItemCard } from "./ItemCard";
interface ItemListProps {
  items: ItemCardProps[];
}
export function ItemList({ items }: ItemListProps) {
  return (
    <Box>
      <SimpleGrid cols={6}>
        {items.map((item) => (
          <ItemCard {...item} key={item.id}></ItemCard>
        ))}
      </SimpleGrid>
    </Box>
  );
}
