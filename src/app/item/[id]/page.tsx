import { use } from "react";
import { useItem } from "../../hooks/useItem";

export default function ItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: item, isLoading, isError } = useItem(id);
}
