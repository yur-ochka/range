// import { useQuery } from "@tanstack/react-query";
// import api from "../lib/api/axiosInstance";

// export function useItem(id: string) {
//   return useQuery<Item>({
//     queryKey: ["item", id],
//     queryFn: async () => {
//       const response = await api.get(`/api/items/${id}`);
//       return response.data;
//     },
//     retry: false,
//   });
// }
