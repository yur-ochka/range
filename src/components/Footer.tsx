import {
  Container,
  Grid,
  GridCol,
  Text,
  Group,
  Anchor,
  Table,
  List,
  ListItem,
  rem,
} from "@mantine/core";
import {
  IconBrandFacebook,
  IconBrandLinkedin,
  IconBrandYoutube,
  IconBrandInstagram,
} from "@tabler/icons-react";

export default function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid #e9ecef",
        marginTop: rem(40),
        padding: "2rem 0",
      }}
    >
      <Container size="lg">
        <Grid>
          <GridCol span={{ base: 12, sm: 4 }}>
            <Text fw={500} size="lg" mb="md">
              Range
            </Text>

            <List spacing="xs" listStyleType="none" withPadding={false}>
              <ListItem>
                <Group>
                  <IconBrandFacebook size={18} />
                  <Anchor href="#" size="sm" color="dimmed">
                    Facebook
                  </Anchor>
                </Group>
              </ListItem>
              <ListItem>
                <Group>
                  <IconBrandLinkedin size={18} />
                  <Anchor href="#" size="sm" color="dimmed">
                    LinkedIn
                  </Anchor>
                </Group>
              </ListItem>
              <ListItem>
                <Group>
                  <IconBrandYoutube size={18} />
                  <Anchor href="#" size="sm" color="dimmed">
                    YouTube
                  </Anchor>
                </Group>
              </ListItem>
              <ListItem>
                <Group>
                  <IconBrandInstagram size={18} />
                  <Anchor href="#" size="sm" color="dimmed">
                    Instagram
                  </Anchor>
                </Group>
              </ListItem>
            </List>
          </GridCol>

          <GridCol span={{ base: 12, sm: 8 }}>
            <Table withColumnBorders={false} highlightOnHover={false}>
              <thead>
                <tr>
                  <th>Topic</th>
                  <th>Topic</th>
                  <th>Topic</th>
                  <th>Topic</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Page</td>
                  <td>Page</td>
                  <td>Page</td>
                  <td>Page</td>
                </tr>
                <tr>
                  <td>Page</td>
                  <td>Page</td>
                  <td>Page</td>
                  <td>Page</td>
                </tr>
                <tr>
                  <td>Page</td>
                  <td>Page</td>
                  <td>Page</td>
                  <td>Page</td>
                </tr>
              </tbody>
            </Table>
          </GridCol>
        </Grid>

        <Text ta="center" size="xs" color="dimmed" mt="md">
          © 2025 Range. All rights reserved.
        </Text>
      </Container>
    </footer>
  );
}
