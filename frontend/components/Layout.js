import Link from "next/link";
import { useRouter } from "next/router";
import { api, clearToken } from "../lib/api";

const navItems = [
    { href: "/dashboard", icon: "⚡", label: "Dashboard" },
    { href: "/profile", icon: "👤", label: "Profile" },
    { href: "/templates", icon: "🧩", label: "Templates" },
    { href: "/resume-builder", icon: "📄", label: "Resume Builder" },
    { href: "/resume-history", icon: "🕓", label: "Resume History" },
    { href: "/jobs", icon: "🎯", label: "Job Tracker" },
    { href: "/cover-letter", icon: "✉️", label: "Cover Letter" },
    { href: "/ai", icon: "🤖", label: "AI Writer" },
];

export default function Layout({ children }) {
    const router = useRouter();

    async function handleLogout() {
        try {
            await api.logout();
        } catch (_) {
            // no-op
        }
        clearToken();
        router.push("/login");
    }

    return (
        <div className="layout">
            <aside className="sidebar">
                <div className="logo">CareerForge<span> Pro</span></div>
                <nav>
                    {navItems.map((item) => (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`nav-link ${router.pathname === item.href ? "active" : ""}`}
                        >
                            <span className="nav-icon">{item.icon}</span>
                            {item.label}
                        </Link>
                    ))}
                </nav>
                <div style={{ marginTop: "auto", padding: "12px 8px" }}>
                    <button className="btn btn-secondary btn-sm" onClick={handleLogout} style={{ width: "100%", marginBottom: "12px" }}>
                        Logout
                    </button>
                    <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", lineHeight: 1.6 }}>
                        Powered by<br />
                        <span style={{ color: "var(--accent-violet)" }}>Groq Cloud</span>
                    </div>
                </div>
            </aside>
            <main className="main-content">{children}</main>
        </div>
    );
}
