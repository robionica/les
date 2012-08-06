struct boost::edge_component_t edge_component;

/**
 * This algorithm provides decomposition of interaction graph
 * by articulation points and returns a vector of blocks.
 *
 * Please follow this link
 * http://www.boost.org/doc/libs/1_35_0/libs/graph/doc/biconnected_components.html
 * in order to learn more about biconnected components and
 * articulation points.
 */
vector<Block*>*
block_decomposition_by_articulation_points(InteractionGraph* g)
{
#if 0
  using namespace boost;
  std::vector<vertex_t> art_points;
  MILPP* problem = g->get_problem();

  property_map < graph_t, edge_component_t >::type
    component = get(edge_component, *(graph_t*)g);
  std::size_t num_comps = biconnected_components(*(graph_t*)g, component);
  std::cerr << "Found " << num_comps << " biconnected components.\n";

  /* Get articulation points */
  articulation_points(*(graph_t*)g, std::back_inserter(art_points));
  printf("Found %d articulation point(s)\n", art_points.size());

  /* Sort articulation points */
  sort(art_points.begin(), art_points.end());
  art_points.push_back(problem->get_num_cols());

  Block* curr_block;
  Block* last_block = NULL;
  vector<Block*>* blocks = new vector<Block*>();

  for (size_t i = 0; i < art_points.size(); i++)
    {
      curr_block = new Block();
      curr_block->set_left_indices(last_block ? last_block->get_right_indices() : NULL);

      unsigned v = 0;

      if (curr_block->get_left_indices())
        {
          v = curr_block->get_left_indices()->back() + 1;
        }

      do {
        curr_block->get_middle_indices()->push_back(v);
        v++;
      } while (v < art_points[i]);

      if (art_points[i] != (size_t)problem->get_num_cols())
        {
          unsigned j = i;
          do {
            if ((j - i) != (art_points[j] - art_points[i]))
              break;
            curr_block->get_right_indices()->push_back(art_points[j]);
            j++;
          } while (j < art_points.size());
          i = j - 1;
        }

      /* Form list of constraints that include our variables from used
         blocks */
      for (int i = 0; i < problem->get_num_rows(); i++)
        for (unsigned j = 0; j < curr_block->get_middle_indices()->size(); j++)
          if (problem->get_row(i)->get_elements()[curr_block->get_middle_indices()->at(j)])
            {
              curr_block->get_row_indices()->push_back(i);
              break;
            }

      blocks->push_back(curr_block);
      last_block = curr_block;
    }

  return blocks;
#endif
  return NULL;
}
