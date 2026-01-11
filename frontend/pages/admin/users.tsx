import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import api from '../../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_staff: boolean;
  is_active: boolean;
  first_name: string;
  last_name: string;
}

const UsersManagementPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    role: 'cashier',
    first_name: '',
    last_name: ''
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/accounts/users/');
      setUsers(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/accounts/users/', newUser);
      setShowCreateModal(false);
      setNewUser({ username: '', email: '', password: '', role: 'cashier', first_name: '', last_name: '' });
      fetchUsers();
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Failed to create user');
    }
  };

  const handleDeleteUser = async (id: number) => {
    if (confirm('Are you sure you want to delete this user?')) {
      try {
        await api.delete(`/accounts/users/${id}/`);
        fetchUsers();
      } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user');
      }
    }
  };

  const getRoleBadgeColor = (role: string) => {
    const colors: { [key: string]: string } = {
      owner: 'bg-purple-600',
      admin: 'bg-red-600',
      manager: 'bg-blue-600',
      cashier: 'bg-green-600',
      teacher: 'bg-yellow-600',
      parent: 'bg-gray-600'
    };
    return colors[role] || 'bg-gray-600';
  };

  return (
    <>
      <Head>
        <title>User Management | Admin Panel</title>
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 p-6">
        {/* Header */}
        <div className="max-w-7xl mx-auto mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">👥 User Management</h1>
              <p className="text-gray-400">Manage system users and their roles</p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition-all duration-200 flex items-center space-x-2"
              >
                <span>+</span>
                <span>Add User</span>
              </button>
              <a
                href="/"
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
              >
                ← Back
              </a>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-2xl border border-gray-700 overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center p-12">
                <div className="text-white text-xl">Loading users...</div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-900 border-b border-gray-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">User</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Email</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Role</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Status</th>
                      <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Staff</th>
                      <th className="px-6 py-4 text-right text-sm font-semibold text-gray-300">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id} className="border-b border-gray-800 hover:bg-gray-800/50 transition-colors duration-200">
                        <td className="px-6 py-4">
                          <div className="flex items-center space-x-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center text-white font-bold">
                              {user.username.charAt(0).toUpperCase()}
                            </div>
                            <div>
                              <div className="text-white font-medium">{user.username}</div>
                              <div className="text-gray-400 text-sm">{user.first_name} {user.last_name}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-300">{user.email}</td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-white text-xs font-semibold ${getRoleBadgeColor(user.role)}`}>
                            {user.role.toUpperCase()}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {user.is_active ? (
                            <span className="px-3 py-1 rounded-full bg-green-900/30 text-green-400 text-xs font-semibold">
                              ● Active
                            </span>
                          ) : (
                            <span className="px-3 py-1 rounded-full bg-red-900/30 text-red-400 text-xs font-semibold">
                              ● Inactive
                            </span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          {user.is_staff ? (
                            <span className="text-blue-400">✓ Staff</span>
                          ) : (
                            <span className="text-gray-500">—</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleDeleteUser(user.id)}
                            className="px-3 py-1 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded transition-colors duration-200 text-sm"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Create User Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-8 max-w-md w-full mx-4 border border-gray-700 shadow-2xl">
              <h2 className="text-2xl font-bold text-white mb-6">Create New User</h2>
              <form onSubmit={handleCreateUser}>
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-300 text-sm font-semibold mb-2">Username *</label>
                    <input
                      type="text"
                      required
                      value={newUser.username}
                      onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                      className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-semibold mb-2">Email *</label>
                    <input
                      type="email"
                      required
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-semibold mb-2">Password *</label>
                    <input
                      type="password"
                      required
                      value={newUser.password}
                      onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                      className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-gray-300 text-sm font-semibold mb-2">First Name</label>
                      <input
                        type="text"
                        value={newUser.first_name}
                        onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                    </div>
                    <div>
                      <label className="block text-gray-300 text-sm font-semibold mb-2">Last Name</label>
                      <input
                        type="text"
                        value={newUser.last_name}
                        onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                        className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm font-semibold mb-2">Role *</label>
                    <select
                      required
                      value={newUser.role}
                      onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                      className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    >
                      <option value="cashier">Cashier</option>
                      <option value="manager">Manager</option>
                      <option value="admin">Admin</option>
                      <option value="owner">Owner</option>
                    </select>
                  </div>
                </div>
                <div className="flex items-center justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition-all duration-200"
                  >
                    Create User
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default UsersManagementPage;

// Disable static optimization to avoid prerender errors on Vercel
export async function getServerSideProps() {
  return { props: {} }
}
