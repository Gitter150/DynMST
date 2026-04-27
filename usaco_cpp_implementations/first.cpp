#include <bits/stdc++.h>
using namespace std;

/*
A link cut tree is a data structure that uses splay trees to represent a forest of rooted trees and can perform the following operations with an amortized upper bound time complexity of 
O(logN):

Linking a tree with a node by making the root of the tree a child of any node of another tree
Deleting the edge between a node and its parent, detaching the node's subtree to make a new tree
Find the root of the tree that a node belongs to
These operations all use the access(v) subroutine, which creates a preferred path from the root of the represented tree to vertex 
v, making a corresponding auxiliary splay tree with v as the root.

Solution
With Link Cut Tree
We can use a link cut tree to process each type of query 
O(logN) time. Adding an edge or removing an edge between two vertices are standard features of the link cut tree.

Checking if there's a path between two nodes is the same as checking if they're part of the same tree. To check if two nodes are part of the same tree, we can check if the roots of the trees of the two nodes are the same.

Here is the implementation of a link cut tree in C++:
*/

struct Node {
	int x;
	Node *l = 0;
	Node *r = 0;
	Node *p = 0;
	bool rev = false;

	Node() = default;

	Node(int v) { x = v; }

	void push() {
		if (rev) {
			rev = false;
			swap(l, r);
			if (l) l->rev ^= true;
			if (r) r->rev ^= true;
		}
	}

	bool is_root() { return p == 0 || (p->l != this && this != p->r); }
};

struct LCT {
	vector<Node> a;

	LCT(int n) {
		a.resize(n + 1);
		for (int i = 1; i <= n; ++i) a[i].x = i;
	}

	void rot(Node *c) {
		auto p = c->p;
		auto g = p->p;

		if (!p->is_root()) (g->r == p ? g->r : g->l) = c;

		p->push();
		c->push();

		if (p->l == c) {  // rtr
			p->l = c->r;
			c->r = p;
			if (p->l) p->l->p = p;
		} else {  // rtl
			p->r = c->l;
			c->l = p;
			if (p->r) p->r->p = p;
		}

		p->p = c;
		c->p = g;
	}

	void splay(Node *c) {
		while (!c->is_root()) {
			auto p = c->p;
			auto g = p->p;
			if (!p->is_root()) rot((g->r == p) == (p->r == c) ? p : c);
			rot(c);
		}
		c->push();
	}

	Node *access(int v) {
		Node *last = 0;
		Node *c = &a[v];
		for (Node *p = c; p; p = p->p) {
			splay(p);
			p->r = last;
			last = p;
		}
		splay(c);
		return last;
	}

	void make_root(int v) {
		access(v);
		auto *c = &a[v];
		if (c->l) c->l->rev ^= true, c->l = 0;
	}

	void link(int u, int v) {
		make_root(v);
		Node *c = &a[v];
		c->p = &a[u];
	}

	void cut(int u, int v) {
		make_root(u);
		access(v);
		if (a[v].l) {
			a[v].l->p = 0;
			a[v].l = 0;
		}
	}

	bool connected(int u, int v) {
		access(u);
		access(v);
		return a[u].p;
	}
};
// EndCodeSnip

int main() {
	int n;
	int m;
	cin >> n >> m;
	LCT lc(n);

	for (int i = 0; i < m; i++) {
		string a;
		cin >> a;
		int b, c;
		cin >> b >> c;
		if (a == "add") { lc.link(b, c); }
		if (a == "rem") { lc.cut(b, c); }
		if (a == "conn") { cout << (lc.connected(b, c) ? "YES" : "NO") << "\n"; }
	}
}