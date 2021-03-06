#!/usr/bin/env ruby

require 'set'

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

  def sample!
    delete_at rand length
  end
end

class DiGraph
  attr_accessor :nodes, :attacks
  def initialize nodes
    @nodes = nodes
    @attacks = Set.new
  end

  def add_attack attacker, target
    @attacks.add [attacker, target] if attacker
  end

  def save_as filename
    File.open("../graphs/#{filename}", "w") do |f|
      f.puts @nodes.join " "
      @attacks.each do |att|
        f.puts att.join " "
      end
    end
  end
end

def generate_node_names node_count
  names = []
  (1..node_count).each do |i|
    names.enqueue i.to_s
  end
  return names
end

def fully_connected_builder names
  graph = DiGraph.new(names)
  names.each do |target|
    names.each do |attacker|
      graph.add_attack attacker, target
    end
  end
  return graph
end

def random_graph_builder names
  graph = DiGraph.new(names)
  name_count = names.length
  max_edge_count = (name_count*(name_count-1))/2 # fully connected num
  rng = Random.new
  edge_count = rng.rand(name_count..max_edge_count)
  edge_count.times do
    attacker = names.sample
    target = nil
    loop do
      target = names.sample
      break if target != attacker
    end
    graph.add_attack attacker, target
  end
  return graph
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

def unbalanced_tree_builder names, branches_count
  graph = DiGraph.new(names)
  next_root = [names.first] * branches_count
  _, *unused_leaves = names.clone

  while unused_leaves.any?
    target = next_root.sample!
    leaf = unused_leaves.dequeue
    branches_count.times { next_root.enqueue leaf }
    graph.add_attack leaf, target
  end
  return graph
end

def worst_case_tree_builder names, branches_count
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

def looping_graph_builder names
  graph = DiGraph.new(names)
  next_root = [names.first]
  _, *unused_leaves = names.clone << names.first

  while unused_leaves.any?
    target = next_root.dequeue
    leaf = unused_leaves.dequeue
    next_root.enqueue leaf
    graph.add_attack leaf, target
  end
  return graph
end

# puts "use: ruby digraph_gen.rb nodes type"
# puts "type: one of x y z"
# desired_node_count = ARGV[0].to_i
# branches_count = ARGV[1].to_i

# names = generate_node_names desired_node_count
# graph = balanced_tree_builder names, branches_count
# graph.save_as "balanced_tree"
# graph = worst_case_tree_builder names, branches_count
# graph.save_as "worst_case_tree"
# graph = looping_graph_builder names
# graph.save_as "looping_graph"
# graph = unbalanced_tree_builder names, branches_count
# graph.save_as "unbalanced_tree"

(50..450).step(200) do |node_count|
# (5..95).step(10) do |node_count|
  names = generate_node_names node_count
  graph = looping_graph_builder names
  graph.save_as "looping_graph_#{node_count}"
  graph = balanced_tree_builder names, 2
  graph.save_as "balanced_binary_tree_#{node_count}"
  graph = balanced_tree_builder names, 20
  graph.save_as "balanced_20_tree_#{node_count}"
  graph = worst_case_tree_builder names, 2
  graph.save_as "worst_case_tree_#{node_count}"
  graph = random_graph_builder names
  graph.save_as "random_graph_#{node_count}"
  # graph = fully_connected_builder names
  # graph.save_as "fully_connected_graph_#{node_count}"
end
