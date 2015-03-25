#!/usr/bin/env ruby

class Array
  def dequeue
    self.shift
  end

  def enqueue obj
    self.push obj
  end

  def tail
    self[1..-1]
  end
end

class DiGraph
  attr_accessor :nodes, :attacks
  def initialize nodes
    @nodes = nodes
    @attacks = []
  end

  def add_attack attacker, target
    @attacks.enqueue [attacker, target] if attacker
  end

  def save_as filename
    File.open(filename, "w") do |f|
      f.puts @nodes.join " "
      @attacks.each do |att|
        f.puts att.join " "
      end
    end
  end
end

def generate_node_names node_count
  names = []
  (0..node_count).each do |i|
    names.enqueue i.to_s
  end
  return names
end

def balanced_tree_builder names, branches_count
  graph = DiGraph.new(names)
  next_root = [names.first] * branches_count
  _, *unused_leaves = names.clone

  while unused_leaves.any?
    target = next_root.dequeue
    leaf = unused_leaves.dequeue
    branches_count.times { next_root.enqueue leaf }
    graph.add_attack leaf, target
  end
  return graph
end

def worst_case_tree names, branches_count
  graph = DiGraph.new(names)
  next_root = [names.first] * branches_count
  _, *unused_leaves = names.clone

  while unused_leaves.any?
    target = next_root.dequeue
    leaf = unused_leaves.dequeue
    rebut_leaf = unused_leaves.dequeue
    graph.add_attack leaf, target
    graph.add_attack rebut_leaf, leaf
    branches_count.times { next_root.enqueue rebut_leaf }
  end
  return graph
end

puts "use: ruby digraph_gen.rb nodes type"
puts "type: one of x y z"
desired_node_count = ARGV[0].to_i
branches_count = ARGV[1].to_i

names = generate_node_names desired_node_count
graph = balanced_tree_builder names, branches_count
graph.save_as "balanced_tree"
graph = worst_case_tree names, branches_count
graph.save_as "worst_case_tree"
