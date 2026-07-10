import {
  MessageSquare, Send, Layers, Users, Zap, Inbox, LibraryBig, LineChart, Plug, Shield, HeartHandshake,
  Search, Radio, Wallet, ShoppingBag, Boxes, ClipboardList, UserRound, Bot, Mic, Truck, Home,
  UserPlus, GitBranch, Handshake, Activity, FolderLock, Bell, PiggyBank,
  ClipboardCheck, FileText, Beaker, ShieldCheck, Building, Route, Sun, Layers3, GraduationCap,
  Code2, Video, BookOpen, Database, BrainCircuit, PhoneCall, Network, FileSearch, Waypoints, Cpu, Sparkles
} from "lucide-react";

const map = new Map([
  ["Brand Onboarding", HeartHandshake],
  ["Message Types", MessageSquare],
  ["Mass Scale Broadcasting", Radio],
  ["Segmentation & Targeting", Layers],
  ["Automation & Journeys", Zap],
  ["Two-Way Inbox", Inbox],
  ["Templates Management", LibraryBig],
  ["Analytics & Reporting", LineChart],
  ["Integrations", Plug],
  ["Compliance & Safety", Shield],
  ["Managed Services", Users],

  ["Influencer Discovery", Search],
  ["Communication & Hub", MessageSquare],
  ["Campaign Management", ClipboardList],
  ["Live Tracking", Activity],
  ["Analytics & ROI", LineChart],
  ["Affiliate Marketing", Send],
  ["Payments & Compliance", Wallet],

  ["Product & Inventory", Boxes],
  ["Order Lifecycle", ShoppingBag],
  ["CRM & Retention", UserRound],
  ["Marketing Workflows", Zap],
  ["Conversational AI", Bot],
  ["Voice Agents", Mic],
  ["Data Analytics", LineChart],
  ["Supply Chain Intel", Truck],

  ["Property Listings Management", Home],
  ["Lead Management", UserPlus],
  ["Customer Journey Tracking", GitBranch],
  ["Partner Ecosystem", Handshake],
  ["Project Analytics", Activity],
  ["Document Vault", FolderLock],
  ["Automated Communication", Bell],
  ["Finance Tracking", PiggyBank],

  ["Quality Dashboards", ClipboardCheck],
  ["Batch Records Review Tool", FileText],
  ["Protocol Preparation Tools", Beaker],
  ["CPV Tool", Activity],
  ["APQR Reporting Tool", LineChart],
  ["Assessment Tool", ShieldCheck],

  ["Unified City Data Platform", Building],
  ["Smart Mobility Intelligence", Route],
  ["Utility & Resource Management", Sun],

  ["College LMS", GraduationCap],
  ["Groups & Cohort Management", Users],
  ["Course Learning Experience", BookOpen],
  ["Test Series Platform", ClipboardList],
  ["Coding LMS", Code2],
  ["Video LMS", Video],

  ["RAG & Agentic Applications", BrainCircuit],
  ["Conversational AI ", Bot],
  ["Voice Agents ", PhoneCall],
  ["Multi-Agent Systems", Network],
  ["Document AI", FileSearch],
  ["Data Engineering & Analytics", Database],
  ["Agentic Knowledge Graph", Waypoints],
  ["Database Agents", Database],
  ["Fine-Tuning & RL", Cpu],
]);

export default function CapabilityIcon({ label, className = "h-9 w-9" }) {
  const Icon = map.get(label) || Sparkles;
  return (
    <div className={`rounded-xl grid place-items-center ${className}`}
      style={{ background: "color-mix(in oklab, var(--accent) 12%, transparent)", border: "1px solid color-mix(in oklab, var(--accent) 25%, transparent)" }}>
      <Icon className="h-4 w-4" style={{ color: "var(--accent)" }} />
    </div>
  );
}
