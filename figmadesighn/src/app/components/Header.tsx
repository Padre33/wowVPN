import { Search, Bell, Globe, LogOut } from "lucide-react";

interface HeaderProps {
  onSearchOpen: () => void;
}

export function Header({ onSearchOpen }: HeaderProps) {
  return (
    <header className="h-16 border-b border-border bg-card flex items-center justify-between px-6">
      <button
        onClick={onSearchOpen}
        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-input text-muted-foreground hover:bg-muted transition-colors"
      >
        <Search className="w-4 h-4" />
        <span className="text-sm">Search users, configs...</span>
        <kbd className="ml-auto text-xs bg-muted px-2 py-1 rounded">⌘K</kbd>
      </button>

      <div className="flex items-center gap-2">
        <button className="p-2 rounded-lg hover:bg-muted transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-destructive rounded-full"></span>
        </button>
        <button className="p-2 rounded-lg hover:bg-muted transition-colors">
          <Globe className="w-5 h-5" />
        </button>
        <button className="p-2 rounded-lg hover:bg-destructive/20 text-destructive transition-colors">
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  );
}
