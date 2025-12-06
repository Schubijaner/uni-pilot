import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  // Onboarding als Index-Route
  index("routes/onboarding.tsx"),
  // Selection View
  route("selection", "routes/selection.tsx"),
  // Roadmap View
  route("roadmap", "routes/roadmap.tsx"),
  route("login", "routes/login.tsx"),
] satisfies RouteConfig;
