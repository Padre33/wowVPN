import { Command } from "cmdk";
import { Search, X } from "lucide-react";
import { useEffect } from "react";

interface GlobalSearchProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GlobalSearch({ open, onOpenChange }: GlobalSearchProps) {
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        onOpenChange(!open);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [open, onOpenChange]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-start justify-center pt-20 z-50">
      <Command className="w-full max-w-2xl bg-card border border-border rounded-lg shadow-2xl">
        <div className="flex items-center border-b border-border px-4">
          <Search className="w-5 h-5 text-muted-foreground" />
          <Command.Input
            placeholder="Search users, configs, nodes..."
            className="w-full px-4 py-4 bg-transparent outline-none text-foreground placeholder:text-muted-foreground"
          />
          <button
            onClick={() => onOpenChange(false)}
            className="p-1 hover:bg-muted rounded"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <Command.List className="max-h-96 overflow-y-auto p-2">
          <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
            No results found.
          </Command.Empty>
          <Command.Group heading="Users" className="text-muted-foreground text-xs px-2 py-1">
            <Command.Item className="px-4 py-2 rounded hover:bg-muted cursor-pointer">
              user_premium_001
            </Command.Item>
            <Command.Item className="px-4 py-2 rounded hover:bg-muted cursor-pointer">
              user_family_vip
            </Command.Item>
          </Command.Group>
          <Command.Group heading="Nodes" className="text-muted-foreground text-xs px-2 py-1 mt-2">
            <Command.Item className="px-4 py-2 rounded hover:bg-muted cursor-pointer">
              node-eu-01 (Amsterdam)
            </Command.Item>
            <Command.Item className="px-4 py-2 rounded hover:bg-muted cursor-pointer">
              node-us-02 (New York)
            </Command.Item>
          </Command.Group>
        </Command.List>
      </Command>
    </div>
  );
}
