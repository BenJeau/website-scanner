import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";
import { QueryClient } from "@tanstack/react-query";

import type { paths } from "@/lib/openapi";

const fetchClient = createFetchClient<paths>({
  baseUrl: "http://localhost:8000",
});

export const queryClient = new QueryClient();
export const $api = createClient(fetchClient);